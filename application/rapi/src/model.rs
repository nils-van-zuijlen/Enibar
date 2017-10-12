use diesel::prelude::*;
use validator::Validate;
use errors::*;

pub trait Model<'a> where
    Self: ::diesel::associations::HasTable + Sized + Validate + 'a
{
    fn save(self, conn: &PgConnection) -> Result<Self>;
    fn all(conn: &PgConnection) -> Result<Vec<Self>>;
}
