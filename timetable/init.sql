CREATE TABLE worker
(
    id           serial PRIMARY KEY,
    full_name    text not null,
    work_start   time without time zone,
    work_end     time without time zone,
    today_work   boolean,
    fully_loaded boolean
);

create TABLE if not exists task
(
    id         serial PRIMARY KEY,
    worker_id  int,
    time_start time without time zone not null,
    time_end   time without time zone not null,
    duration   interval               not null,
    FOREIGN KEY (worker_id) REFERENCES worker (id)
);