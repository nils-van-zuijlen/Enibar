use validator::ValidationErrors;

error_chain!{
    foreign_links {
        DieselError(::diesel::result::Error);
        BcryptError(::bcrypt::BcryptError);
        R2d2Error(::r2d2::Error);
    }

    errors {
        ValidationError(t: ValidationErrors) {
            description("Validation failed")
            display("Failed to validate this model") // TODO: Use t and provide a better error message
        }
        UserCreationError(t: String) {
            description("The user creation failed")
            display("Failed to create this user: {}", t)
        }
        CategoryCreationError(t: String) {
            description("The category creation failed")
            display("Failed to create this category: {}", t)
        }
    }
}
