use errors::*;
use diesel::prelude::*;
use diesel::associations::HasTable;

pub trait Model<'a> where
    Self: Sized + HasTable + 'a {
    fn save(self, conn: &PgConnection) -> Result<Self>;
    fn all(conn: &PgConnection) -> Result<Vec<Self>>;
}
