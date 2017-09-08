table!(
    admins(login) {
        login -> Text,
        password -> Text,
        manage_notes -> Bool,
        manage_users -> Bool,
        manage_products -> Bool,
    }
);
