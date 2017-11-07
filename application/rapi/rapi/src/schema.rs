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

table! {
    products(id) {
        id -> Int4,
        name -> Varchar,
        category -> Int4,
        percentage -> Numeric,
    }
}

table! {
    panel_content (panel_id, product_id) {
        panel_id -> Int4,
        product_id -> Int4,
    }
}

joinable!(panel_content -> panels (panel_id));
joinable!(panel_content -> products (product_id));
