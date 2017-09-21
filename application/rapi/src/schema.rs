table!(
    admins(login) {
        login -> Text,
        password -> Text,
        manage_notes -> Bool,
        manage_users -> Bool,
        manage_products -> Bool,
    }
);

table!(
    categories(id) {
        id -> Int4,
	    name -> Text,
	    color -> Text,
	    alcoholic -> Bool,
    }
);
