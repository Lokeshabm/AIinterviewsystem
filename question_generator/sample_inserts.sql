-- Sample SQL inserts for the example question
INSERT INTO branches (id, code, name) VALUES (1,'CSE','Computer Science Engineering') ON CONFLICT DO NOTHING;
INSERT INTO subjects (id, branch_id, code, name, year) VALUES (1,1,'CSE_DS','Data Structures',2) ON CONFLICT DO NOTHING;

INSERT INTO questions (question_uid, branch_id, subject_id, topic_id, qtype, difficulty, statement, canonical_hash, estimated_time, marks, approved, created_at)
VALUES ('11111111-1111-1111-1111-111111111111',1,1,NULL,'MCQ',1,'Given a binary search tree with 100 nodes, what is the average time complexity of search?','e3b0c44298fc1c149afbf4c8996fb924',5,2,true,'2026-06-07T00:00:00Z');

INSERT INTO mcq_options (question_uid, label, option_text, is_correct) VALUES ('11111111-1111-1111-1111-111111111111','A','O(1)',false);
INSERT INTO mcq_options (question_uid, label, option_text, is_correct) VALUES ('11111111-1111-1111-1111-111111111111','B','O(log n)',true);
INSERT INTO mcq_options (question_uid, label, option_text, is_correct) VALUES ('11111111-1111-1111-1111-111111111111','C','O(n)',false);
INSERT INTO mcq_options (question_uid, label, option_text, is_correct) VALUES ('11111111-1111-1111-1111-111111111111','D','O(n log n)',false);
