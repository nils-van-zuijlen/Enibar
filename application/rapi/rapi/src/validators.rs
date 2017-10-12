use validator::ValidationError;

pub(crate) fn not_empty(data: &str) -> Result<(), ValidationError> {
    if data.trim() == "" {
        return Err(ValidationError::new("This field cannot be empty".into()))
    }

    Ok(())
}
