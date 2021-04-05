import os, sys
import cv2
import numpy as np
from openvino.inference_engine import IEPlugin
from lib.queries.mysql_queries import mysql_queries as query
from scope import log, config, features_set, executor, bus, infer

# FeatureSet block
vino_plugin = IEPlugin("CPU")


class FaceExtractError(Exception):
    """Base exception for face features extraction operations"""


class NoFacesException(FaceExtractError):
    """Exception for case when no faces were found"""


class TooManyFacesException(FaceExtractError):
    """Exception for case when more than one face was found"""


class WrongFileTypeException(FaceExtractError):
    """Exception for files cv2 can not read"""


def get_features_from_file(file_path):
    """Get features for faces in the image by path

    Accepts
    -------
    file_path: Str/Path-like object

    Returns
    -------
    256-dim vector or None

    Raises
    ------
    AssertionError: if file does not exist or is a directory
    AttributeError: if file is corrupted or is not a jpeg image
    """
    log.debug('checking if file "{}" exists'.format(file_path))
    assert (os.path.isfile(file_path))
    log.debug('reading file "{}"'.format(file_path))
    frame_binary = cv2.imread(file_path)
    if frame_binary is None:
        raise WrongFileTypeException("Файл повреждён или не является изображением")
    faces = infer.infer_frame(frame_binary)
    if not faces:
        raise NoFacesException("Не найдено ни одного лица")
    if len(faces) > 1:
        raise TooManyFacesException("Более одного лица")
    return faces[0]["features"]


def on_file_added(*args, **kwargs):
    assert (kwargs.get("filename"))
    assert (kwargs.get("old_filename"))
    assert (kwargs.get("transaction_id"))
    assert (kwargs.get("is_tester") is not None)
    log.debug("New file added: {} received".format(kwargs))
    filename = kwargs["filename"]
    old_filename = kwargs["old_filename"]
    destination_topic = kwargs["transaction_id"]
    is_tester = kwargs["is_tester"]
    file_path = os.path.join("/tmp/", filename)
    photos_dir = config.find('photos_dir')
    destination_path = os.path.join(photos_dir, filename)
    try:
        new_face_features = get_features_from_file(file_path)
    except AssertionError as e:
        log.warning('file "{}": {}'.format(file_path, e))
        bus.push(destination_topic, filename=filename, old_filename=old_filename, processed=False,
                 error_message="Файл не найден")
        return
    except AttributeError as e:
        log.warning('failed to read from file "{}": {}'.format(file_path, e))
        bus.push(destination_topic, filename=filename, old_filename=old_filename, processed=False,
                 error_message="Загруженный файл не является изображением в формате jpeg")
        return
    except FaceExtractError as e:
        bus.push(destination_topic, filename=filename, old_filename=old_filename, processed=False,
                 error_message=str(e))
        return
    try:
        os.rename(file_path, destination_path)
    except OSError as e:
        bus.push(destination_topic, filename=filename, old_filename=old_filename, processed=False,
                 error_message=str(e))
        return
    faces = executor.execute_query(query, 'select_faces', commit=True)
    labels_list = [row[2] for row in faces]
    new_face_label = max(labels_list) + 1
    labels_list.append(new_face_label)
    features_list = []
    for idx, row in enumerate(faces):
        file_path = os.path.join(photos_dir, row[1])
        try:
            features = get_features_from_file(file_path)
        except AssertionError as e:
            log.warning('file "{}": {}'.format(file_path, e))
            del labels_list[idx]
            continue
        except AttributeError as e:
            log.warning('failed to read from file "{}": {}'.format(file_path, e))
            del labels_list[idx]
            continue
        except FaceExtractError as e:
            log.warning('failed to extract features from file "{}": {}'.format(file_path, e))
            del labels_list[idx]
            continue
        features_list.append(features)
    features_list.append(new_face_features)
    features_set.rebuild(np.array(features_list), np.array(labels_list))
    executor.execute_query(query, 'insert_face', filename=filename, label_id=new_face_label, is_tester=is_tester,
                           commit=True)
    bus.push(destination_topic, filename=filename, old_filename=old_filename, processed=True)


def on_file_deleted(*args, **kwargs):
    pk = kwargs["id"]
    filename = kwargs["filename"]
    label_id = kwargs["label_id"]
    destination_topic = kwargs["transaction_id"]
    photos_dir = config.find('photos_dir')
    executor.execute_query(query, "delete_face_by_pk", pk=pk, commit=True)
    faces = executor.execute_query(query, 'select_faces', commit=True)
    labels_list = [row[2] for row in faces]
    features_list = []
    for idx, row in enumerate(faces):
        file_path = os.path.join(photos_dir, row[1])
        try:
            features = get_features_from_file(file_path)
        except AssertionError as e:
            log.warning('file "{}": {}'.format(file_path, e))
            del labels_list[idx]
            continue
        except AttributeError as e:
            log.warning('failed to read from file "{}": {}'.format(file_path, e))
            del labels_list[idx]
            continue
        except FaceExtractError as e:
            log.warning('failed to extract features from file "{}": {}'.format(file_path, e))
            del labels_list[idx]
            continue
        features_list.append(features)
    try:
        os.remove(os.path.join(config.find('photos_dir'), filename))
    except (FileNotFoundError, IsADirectoryError, OSError) as e:
        log.error("api File {} cannot be deleted: {}".format(filename, e))
        bus.push(destination_topic, deleted=False, filename=filename, label_id=label_id, reason=str(e))
        return
    features_set.rebuild(np.array(features_list), np.array(labels_list))
    bus.push(destination_topic, deleted=True, filename=filename, label_id=label_id)


executor.execute_query(query, 'create_faces_table', commit=True)

bus.subscribe("file_added", on_file_added)
bus.subscribe("file_deleted", on_file_deleted)
