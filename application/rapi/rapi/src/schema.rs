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

table! {
    note_categories(id) {
        id -> Int4,
        name -> Varchar,
        hidden -> Bool,
        protected -> Bool,
    }
}

table! {
    panels(id) {
        id -> Int4,
        name -> Varchar,
        hidden -> Bool,
    }
}
