mysql_queries = {
    'drop_table_test': """
drop table if exists test
""",
    'create_table_test': """
create table if not exists test (val VARCHAR(20))
""",
    'insert_test_row': """
insert into test (val) values ('{val}')
""",
    'select_test': """
select * from test where dt >= {time}
""",
    'create_mvideo_db': """
CREATE DATABASE IF NOT EXISTS mvideo
""",
    'use_mvideo_db': """
USE mvideo
""",
    'create_ping_table': """
create table if not exists ping (stage VARCHAR(100), ts DATETIME(6))
""",
    'insert_ping': """
insert into ping (stage, ts) values ('{stage}', '{ts}')
""",
    # ALERTS TABLE STUFF
    'create_alerts_table': """
CREATE TABLE IF NOT EXISTS alerts (
    camera_id VARCHAR(100),
    ts DATETIME(6),
    l INT,
    t INT,
    r INT,
    b INT,
    label INT,
    distance FLOAT,
    frame_number INT,
    filename VARCHAR(100),
    origin VARCHAR(100));
""",
    'alter_is_tester_alerts_table': """
ALTER TABLE alerts ADD `is_tester`  TINYINT(1) DEFAULT 0
""",
    'insert_alerts_table': """
INSERT INTO alerts 
(camera_id, ts, l, t, r, b, label, distance, frame_number, filename, origin, is_tester) VALUES
('{camera_id}', '{ts}', '{l}', '{t}', '{r}', '{b}', '{label}', '{distance}', 
'{frame_number}', '{filename}', '{origin}', '{is_tester}')
""",
    # FRAMES TABLE STUFF
    'create_frames_table': """
CREATE TABLE IF NOT EXISTS frames (
    camera_id VARCHAR(100),
    ts DATETIME(6),
    l INT,
    t INT,
    r INT,
    b INT,
    filename VARCHAR(100),
    frame_number INT,
    features JSON,
    height INT,
    width INT,
    is_read TINYINT(1) DEFAULT 0,
    l_f FLOAT,
    t_f FLOAT,
    r_f FLOAT,
    b_f FLOAT);
""",
    'insert_frames_table': """
INSERT INTO frames 
    (camera_id, ts, l, t, r, b, filename, frame_number, features, height, width, 
    l_f, t_f, r_f, b_f) VALUES 
    ('{camera_id}', '{ts}', '{l}', '{t}', '{r}', '{b}', '{filename}', 
    '{frame_number}', '{features}', '{height}', '{width}', 
    '{l_f}', '{t_f}', '{r_f}', '{b_f}')
""",
    'insert_many_frames': """
INSERT INTO frames 
    (camera_id, ts, l, t, r, b, filename, frame_number, features, height, width, 
    l_f, t_f, r_f, b_f) VALUES 
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""",
    'drop_frames_table': """
DROP TABLE IF EXISTS frames;
""",
    'select_frames_tracker': """
SELECT
    camera_id,
    ts,
    l_f,
    t_f,
    r_f,
    b_f,
    filename,
    frame_number
FROM frames
WHERE is_read = 0
ORDER BY ts
LIMIT {limit};
""",
    'update_frames_status': """
UPDATE frames SET is_read=1 WHERE ts <= STR_TO_DATE('{oldest}', '%Y-%m-%d %H:%i:%s.%f');
""",
    # TRACK TABLE STUFF
    'create_tracks_table': """
CREATE TABLE IF NOT EXISTS tracks (
    track_id VARCHAR(100),
    l0 FLOAT,
    t0 FLOAT,
    r0 FLOAT,
    b0 FLOAT,
    ts0 DATETIME(6),
    filename0 VARCHAR(100),
    frame0 INT,
    l1 FLOAT,
    t1 FLOAT,
    r1 FLOAT,
    b1 FLOAT,
    ts1 DATETIME(6),
    filename1 VARCHAR(100),
    frame1 INT,
    len INT,
    camera_id VARCHAR(100));
""",
    'drop_track_table': """
DROP TABLE IF EXISTS tracks;
""",
    'select_tracks_tracker': """
SELECT
    track_id,
    l0,
    t0,
    r0,
    b0,
    ts0,
    filename0,
    frame0,
    l1,
    t1,
    r1,
    b1,
    ts1,
    filename1,
    frame1,
    len,
    camera_id
FROM tracks
WHERE ts1 >= STR_TO_DATE('{time}', '%Y-%m-%d %H:%i:%s.%f')
ORDER BY ts1;
""",
    'select_tracks_reporter': """
SELECT
    l0,
    t0,
    r0,
    b0,
    ts0,
    filename0,
    frame0,
    l1,
    t1,
    r1,
    b1,
    ts1,
    filename1,
    frame1,
    len,
    camera_id
FROM tracks
WHERE track_id = '{track_id}';
""",
    'update_tracks_tracker': """
UPDATE tracks SET
    l1='{l1}',
    t1='{t1}',
    r1='{r1}',
    b1='{b1}',
    ts1='{ts1}',
    filename1='{filename1}',
    frame1='{frame1}',
    len='{len}'
WHERE track_id = '{track_id}';
""",
    'insert_tracks_tracker': """
INSERT INTO tracks(
    track_id,
    l0,
    t0,
    r0,
    b0,
    ts0,
    filename0,
    frame0,
    l1,
    t1,
    r1,
    b1,
    ts1,
    filename1,
    frame1,
    len,
    camera_id) 
VALUES (
    '{track_id}',
    '{l0}',
    '{t0}',
    '{r0}',
    '{b0}',
    '{ts0}',
    '{filename0}',
    '{frame0}',
    '{l1}',
    '{t1}',
    '{r1}',
    '{b1}',
    '{ts1}',
    '{filename1}',
    '{frame1}',
    '{len}',
    '{camera_id}');
""",
    # faces table stuff
    'create_faces_table': """
CREATE TABLE IF NOT EXISTS faces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(100) NOT NULL UNIQUE,
    label_id INT NOT NULL UNIQUE);
""",
    'alter_is_tester_faces_table': """
  ALTER TABLE faces ADD `is_tester`  TINYINT(1) DEFAULT 0
""",
    'drop_faces_table': """
DROP TABLE IF EXISTS faces;
""",
    'select_faces': """
SELECT
    id,
    filename,
    label_id
FROM faces
ORDER BY label_id
LIMIT 1000;
""",
    'select_faces_with_argument': """
SELECT
    id,
    filename,
    label_id
FROM faces
WHERE is_tester = {is_tester}
ORDER BY label_id
LIMIT 1000;
""",
    'select_filename_by_id': """
SELECT
    filename,
    is_tester
FROM faces 
WHERE label_id = {label}
LIMIT 1;
""",
    'insert_face': """
INSERT INTO faces (
    filename,
    label_id,
    is_tester)
VALUES (
'{filename}', {label_id}, {is_tester});
""",
    'insert_faces': """
INSERT INTO faces (
    filename,
    label_id)
VALUES 
{value_pairs};
""",
    'clear_faces': """
DELETE FROM faces WHERE 1=1;
""",
    'delete_face_by_pk': """
DELETE FROM faces WHERE id = {pk} LIMIT 1;
""",
    'delete_face_by_label_id': """
DELETE FROM faces WHERE label_id = {label_id} LIMIT 1;
""",
    'create_telegram_subscribers_table': """
CREATE TABLE IF NOT EXISTS telegram_subscribers (
    user_id INT,
    mute TINYINT(1) DEFAULT 0);
""",
    'alter_bot_telegram_subscribers_table': """
ALTER TABLE telegram_subscribers ADD `bot`  VARCHAR(100) DEFAULT 'blacklist'
""",
    'insert_telegram_subscriber': """
INSERT INTO telegram_subscribers (
    user_id, bot)
VALUES ({user_id}, '{bot}');
""",
    'delete_telegram_subscriber': """
DELETE FROM telegram_subscribers WHERE user_id = {user_id} and bot = '{bot}' LIMIT 1;
""",
    'select_telegram_subscribers': """
SELECT
    user_id
FROM telegram_subscribers
where bot = '{bot}';
""",
    'select_telegram_subscribers_unmute': """
SELECT
    user_id
FROM telegram_subscribers
where mute = 0 and bot = '{bot}';
""",
    'telegram_subscriber_mute': """
UPDATE telegram_subscribers SET
    mute = 1
WHERE user_id = '{user_id}';
"""
}
