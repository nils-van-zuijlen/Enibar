table! {
    admins (login) {
        login -> Varchar,
        password -> Varchar,
        manage_notes -> Bool,
        manage_users -> Bool,
        manage_products -> Bool,
    }
}

table! {
    categories (id) {
        id -> Int4,
        name -> Varchar,
        color -> Varchar,
        alcoholic -> Bool,
    }
}

table! {
    mail_models (name) {
        name -> Varchar,
        subject -> Text,
        message -> Text,
        filter -> Int4,
        filter_value -> Text,
    }
}

table! {
    note_categories (id) {
        id -> Int4,
        name -> Varchar,
        hidden -> Bool,
        protected -> Bool,
    }
}

table! {
    note_categories_assoc (id) {
        id -> Int4,
        note -> Int8,
        category -> Int4,
    }
}

table! {
    notes (id) {
        id -> Int8,
        nickname -> Varchar,
        lastname -> Varchar,
        firstname -> Varchar,
        mail -> Varchar,
        tel -> Varchar,
        birthdate -> Int4,
        promo -> Varchar,
        photo_path -> Nullable<Varchar>,
        note -> Numeric,
        overdraft_date -> Nullable<Date>,
        ecocups -> Int4,
        last_agio -> Nullable<Date>,
        mails_inscription -> Bool,
        stats_inscription -> Bool,
        agios_inscription -> Bool,
        tot_cons -> Numeric,
        tot_refill -> Numeric,
    }
}

table! {
    panel_content (panel_id, product_id) {
        panel_id -> Int4,
        product_id -> Int4,
    }
}

table! {
    panels (id) {
        id -> Int4,
        name -> Varchar,
        hidden -> Bool,
    }
}

table! {
    price_description (id) {
        id -> Int4,
        label -> Varchar,
        category -> Nullable<Int4>,
        quantity -> Int4,
    }
}

table! {
    prices (id) {
        id -> Int4,
        price_description -> Int4,
        product -> Int4,
        value -> Numeric,
    }
}

table! {
    products (id) {
        id -> Int4,
        name -> Varchar,
        category -> Int4,
        percentage -> Numeric,
    }
}

table! {
    scheduled_mails (name) {
        name -> Varchar,
        active -> Bool,
        filter -> Int4,
        filter_value -> Text,
        sender -> Varchar,
        subject -> Text,
        message -> Text,
        schedule_interval -> Int2,
        schedule_unit -> Varchar,
        schedule_day -> Int2,
        last_sent -> Nullable<Date>,
    }
}

table! {
    transactions (id) {
        id -> Int4,
        date -> Timestamptz,
        note -> Varchar,
        category -> Varchar,
        product -> Varchar,
        price_name -> Varchar,
        price -> Numeric,
        quantity -> Int4,
        lastname -> Varchar,
        firstname -> Varchar,
        deletable -> Bool,
        percentage -> Numeric,
        liquid_quantity -> Int4,
        note_id -> Nullable<Int4>,
    }
}

joinable!(note_categories_assoc -> note_categories (category));
joinable!(note_categories_assoc -> notes (note));
joinable!(panel_content -> panels (panel_id));
joinable!(panel_content -> products (product_id));
joinable!(price_description -> categories (category));
joinable!(prices -> price_description (price_description));
joinable!(prices -> products (product));
joinable!(products -> categories (category));

allow_tables_to_appear_in_same_query!(
    admins,
    categories,
    mail_models,
    note_categories,
    note_categories_assoc,
    notes,
    panel_content,
    panels,
    price_description,
    prices,
    products,
    scheduled_mails,
    transactions,
);
