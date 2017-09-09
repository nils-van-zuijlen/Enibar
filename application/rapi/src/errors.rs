error_chain!{
    foreign_links {
        DieselError(::diesel::result::Error);
        BcryptError(::bcrypt::BcryptError);
        R2d2Error(::r2d2::GetTimeout);
    }

    errors {
        UserCreationError(t: String) {
            description("The user creation failed")
            display("Failed to create this user: {}", t)
        }
    }
}
