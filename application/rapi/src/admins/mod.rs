use diesel::prelude::*;
use bcrypt;


#[derive(Queryable, Debug)]
pub struct Admin {
    pub login: String,
    pub password: String,
    pub manage_notes: bool,
    pub manage_users: bool,
    pub manage_products: bool,
}

impl<'a> Admin {
    pub fn get_filtered(manage_notes: bool, manage_users: bool, manage_products: bool) -> Vec<Admin> {
        use schema::admins;
        let connection = ::DB_POOL.get().unwrap();

        let mut query = admins::table.into_boxed();
        if manage_notes {
            query = query.filter(admins::manage_notes.eq(true));
        }
        if manage_users {
            query = query.filter(admins::manage_users.eq(true));
        }
        if manage_products {
            query = query.filter(admins::manage_products.eq(true));
        }

        query = query.order(admins::login.desc());

        query.load(&*connection).unwrap()
    }

    pub fn is_authorized(username: &'a str, password: &'a str) -> bool {
        use schema::admins;
        let connection = ::DB_POOL.get().unwrap();

        let user: &Admin = &admins::table.find(username).load(&*connection).unwrap()[0];

        bcrypt::verify(password, &user.password).unwrap()
    }
}
