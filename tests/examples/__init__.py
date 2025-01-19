from metabolights_utils.provider.ftp_repository import MetabolightsFtpRepository

if __name__ == "__main__":
    client = MetabolightsFtpRepository()

    studies = client.list_studies()

    meta = client.download_study_metadata_files("MTBLS3", override_local_files=False)
    result = client.download_study_data_files(
        "MTBLS3",
        selected_data_files=["FILES/Cecilia_AA_rerun42.raw"],
        override_local_files=False,
    )
    if result.success:
        model, messages = client.load_study_model(study_id="MTBLS3")
    folder_content, messages = client.get_study_folder_content("MTBLS3")

    model, messages = client.load_study_model(
        study_id="MTBLS3", use_only_local_path=True
    )
