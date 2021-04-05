import os, sys
from flask import Flask, request
from flask_restful import Resource, Api
import flask_cors as cors
from uuid import uuid4 as uuid
from time import time
from scope import bus, log, executor, query, ProgrammingError, InterfaceError, OperationalError, IntegrityError

# Flask + JWT
app = Flask(__name__)
api = Api(app)
cors.CORS(
    app, origins="*", allow_headers=[
        "X-Real-Ip",
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Credentials",
        "X-Custom-Header",
        "Cache-Control",
        "x-Requested-With"
    ],
    supports_credentials=True)


class Photo(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_tester = False

    def get(self):
        try:
            res = executor.execute_query(query, "select_faces_with_argument", is_tester=self.is_tester, commit=True)
        except InterfaceError as e:
            return "Нет соединения с БД", 400
        return res

    def post(self):
        """Add a new photo.

        Accepts
        -------
        request.files: Form data binaries

        Returns
        -------
        {"success": True}: JSON
        """
        transaction_id = str(uuid())
        filenames = []
        for key in request.files:
            file = request.files[key]
            old_filename = file.filename
            filename = str(uuid()) + ".jpg"
            filenames.append(old_filename)
            output_path = os.path.join("/tmp/", filename)
            with open(output_path, "wb"):
                file.save(output_path)
            bus.push("file_added", filename=filename, old_filename=old_filename, transaction_id=transaction_id,
                     is_tester=self.is_tester)
        processed = []
        failed = {}
        start = time()
        while True:
            if time() - start >= 20:
                log.debug("Transaction closed by timeout with {} files left".format(len(filenames)))
                break
            if not len(filenames):
                log.debug("all files processed in {} seconds".format(time() - start))
                break
            raw_msg = bus.client.lpop(transaction_id)

            if raw_msg:
                msg = bus._loads(raw_msg)[1]
                log.debug("new message: {}".format(msg))
                old_filename = msg.get("old_filename")
                if msg["processed"]:
                    processed.append(old_filename)
                    filenames.remove(old_filename)
                else:
                    failed[old_filename] = msg.get("error_message")
                    filenames.remove(old_filename)
        for filename in filenames:
            failed[filename] = "Timeout"
        res = {}
        status = 201
        res["success"] = processed
        if len(failed):
            res["error"] = failed
            status = 207
        log.debug("removing topic {}".format(transaction_id))
        bus.client.delete(transaction_id)
        return res, status

    def delete(self):
        transaction_id = str(uuid())
        pk = int(request.args["id"])
        label_id = int(request.args["label_id"])
        filename = request.args["filename"]
        bus.push("file_deleted", transaction_id=transaction_id, id=pk, filename=filename, label_id=label_id)
        start = time()
        while True:
            if time() - start >= 20:
                log.debug("Transaction closed by timeout, photo id={} not deleted".format(pk))
                return {"success": False, "reason": "Timeout"}, 400
            raw_msg = bus.client.lpop(transaction_id)
            if raw_msg:
                msg = bus._loads(raw_msg)[1]
                bus.client.delete(transaction_id)
                log.debug("new message: {}".format(msg))
                if msg["deleted"]:
                    return msg
                else:
                    return msg, 400


class TesterPhoto(Photo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_tester = True


api.add_resource(Photo, "/api/photo")
api.add_resource(TesterPhoto, "/api/tester_photo")
