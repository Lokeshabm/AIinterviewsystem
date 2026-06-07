-- PostgreSQL schema (core tables simplified)

CREATE TABLE branches (
  id SERIAL PRIMARY KEY,
  code VARCHAR(16) UNIQUE NOT NULL,
  name VARCHAR(128) NOT NULL,
  parent_id INT REFERENCES branches(id)
);

CREATE TABLE subjects (
  id SERIAL PRIMARY KEY,
  branch_id INT REFERENCES branches(id) NOT NULL,
  code VARCHAR(32),
  name VARCHAR(128) NOT NULL,
  year SMALLINT
);

CREATE TABLE topics (
  id SERIAL PRIMARY KEY,
  subject_id INT REFERENCES subjects(id) NOT NULL,
  name VARCHAR(256),
  parent_topic_id INT REFERENCES topics(id)
);

CREATE TABLE questions (
  id BIGSERIAL PRIMARY KEY,
  question_uid UUID NOT NULL UNIQUE,
  branch_id INT REFERENCES branches(id),
  subject_id INT REFERENCES subjects(id),
  topic_id INT REFERENCES topics(id),
  qtype VARCHAR(16),
  difficulty SMALLINT,
  statement TEXT,
  canonical_hash CHAR(64),
  estimated_time INT,
  marks SMALLINT,
  approved BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_questions_branch_subject_diff ON questions (branch_id, subject_id, difficulty);
CREATE UNIQUE INDEX uq_questions_canonical ON questions (canonical_hash);

CREATE TABLE mcq_options (
  id BIGSERIAL PRIMARY KEY,
  question_uid UUID REFERENCES questions (question_uid) ON DELETE CASCADE,
  label CHAR(1),
  option_text TEXT,
  is_correct BOOLEAN
);

CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  name VARCHAR(128) UNIQUE
);

CREATE TABLE question_tags (
  question_id BIGINT REFERENCES questions(id) ON DELETE CASCADE,
  tag_id INT REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (question_id, tag_id)
);

-- JSONB metadata for explanations, keywords
CREATE TABLE question_metadata (
  question_id BIGINT PRIMARY KEY REFERENCES questions(id) ON DELETE CASCADE,
  metadata JSONB
);

-- Suggested GIN index on metadata
CREATE INDEX idx_question_metadata_gin ON question_metadata USING GIN (metadata);
