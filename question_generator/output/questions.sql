-- Sample INSERTs for questions table and mcq_options
INSERT INTO questions (question_uid, branch, subject, topic, qtype, difficulty, statement, canonical_hash, estimated_time, marks, approved, created_at) VALUES ('b5f234d9-8f1b-42ba-8abb-708b90fd6c19','CSE','Data Structures','Binary Search Tree','MCQ','Easy','Given a binary search tree with 119 nodes, what is the average time complexity of search?','7c9c8ca3fc8b566d6d1b6ac9c6aa0c575b9116683efaa06373f77636fc6dc827',5,2 ,true,'2026-06-07T03:02:06.539642Z');
-- options for last question
INSERT INTO mcq_options (question_uid, label, option_text, is_correct) VALUES ('b5f234d9-8f1b-42ba-8abb-708b90fd6c19','A','O(1)',false);
INSERT INTO mcq_options (question_uid, label, option_text, is_correct) VALUES ('b5f234d9-8f1b-42ba-8abb-708b90fd6c19','B','O(log n)',true);
INSERT INTO mcq_options (question_uid, label, option_text, is_correct) VALUES ('b5f234d9-8f1b-42ba-8abb-708b90fd6c19','C','O(n log n)',false);
INSERT INTO mcq_options (question_uid, label, option_text, is_correct) VALUES ('b5f234d9-8f1b-42ba-8abb-708b90fd6c19','D','O(n)',false);
INSERT INTO questions (question_uid, branch, subject, topic, qtype, difficulty, statement, canonical_hash, estimated_time, marks, approved, created_at) VALUES ('63c5a2e6-4033-46a1-a092-141779da8783','ECE','Circuits','Resistors','NUM','Medium','A series circuit has resistors R1=71 ohms and R2=16 ohms. Compute the total resistance.','f3d6180256f1f2f194e5610895a79265595e1da46132734abc8b7f44d90fca22',7,3 ,true,'2026-06-07T03:02:06.540096Z');
INSERT INTO questions (question_uid, branch, subject, topic, qtype, difficulty, statement, canonical_hash, estimated_time, marks, approved, created_at) VALUES ('1c38f4ec-001e-4bba-a9cc-4846af9a1824','CSE','Algorithms','Time Complexity','TF','Easy','The time complexity of binary search is O(log n).','57a407f43730b07f8c745d78ccae196c65d5f66d07f49440a2fa26156e62e009',1,1 ,true,'2026-06-07T03:02:06.540180Z');
-- options for last question
INSERT INTO mcq_options (question_uid, label, option_text, is_correct) VALUES ('1c38f4ec-001e-4bba-a9cc-4846af9a1824','','True',true);
INSERT INTO mcq_options (question_uid, label, option_text, is_correct) VALUES ('1c38f4ec-001e-4bba-a9cc-4846af9a1824','','False',false);
