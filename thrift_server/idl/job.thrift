service JobRPCService{

    void start_scheduler()

    void stop_scheduler()

    void pause_scheduler()

    void resume_scheduler()

    void start_job(1: string job_id)

    void stop_job(1: string job_id)

    void pause_job(1: string job_id)

    void modify_job(1: string job_id, 2: string config)

    void submit_job(1: string file_bytes, 2: string config)
}