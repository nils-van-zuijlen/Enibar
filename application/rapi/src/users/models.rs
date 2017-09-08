use ::schema::admins;

#[derive(Insertable)]
#[table_name="admins"]
pub struct NewUser<'a> {
    pub login: &'a str,
    pub password: &'a str,
}

#[derive(Debug, Queryable, PartialEq)]
pub struct User {
    pub login: String,
    pub password: String,
    pub manage_notes: bool,
    pub manage_users: bool,
    pub manage_products: bool,
}


impl User {
    #[cfg(test)]
    pub fn new(login: &str) -> Self{
        User {
            login: login.into(),
            password: "".into(),
            manage_notes: false,
            manage_users: false,
            manage_products: false,
        }
    }
}
