use byteorder::{NetworkEndian, ReadBytesExt};
use diesel::Queryable;
use diesel::pg::Pg;
use diesel::row::Row;
use diesel::types::*;
use std::error::Error;

use super::models::{NoteCategory, NoteCategorySql};

impl HasSqlType<NoteCategorySql> for Pg {
    fn metadata(_lookup: &Self::MetadataLookup) -> Self::TypeMetadata {
        unreachable!()
    }
}

impl NotNull for NoteCategorySql {}
impl SingleValue for NoteCategorySql {}

expression_impls!(NoteCategorySql -> NoteCategory);

impl Queryable<NoteCategorySql, Pg> for NoteCategory {
    type Row = NoteCategory;

    fn build(row: Self::Row) -> Self {
        row
    }
}

impl FromSqlRow<NoteCategorySql, Pg> for NoteCategory {
    fn build_from_row<T: Row<Pg>>(row: &mut T) -> Result<Self, Box<Error + Send + Sync>> {
        FromSql::<NoteCategorySql, Pg>::from_sql(row.take())
    }
}

impl FromSql<NoteCategorySql, Pg> for NoteCategory {
    fn from_sql(bytes: Option<&[u8]>) -> Result<Self, Box<Error + Send + Sync>> {
        let mut bytes = bytes.unwrap();
        let fields = bytes.read_i32::<NetworkEndian>()?;
        assert_eq!(fields, 4);

        let _type = bytes.read_i32::<NetworkEndian>()?;
        let size = bytes.read_i32::<NetworkEndian>()?;
        assert_eq!(size, 4);
        let category_id = bytes.read_i32::<NetworkEndian>()?;

        let _type = bytes.read_i32::<NetworkEndian>()?;
        let size = bytes.read_i32::<NetworkEndian>()?;
        let (elem_bytes, new_bytes) = bytes.split_at(size as usize);
        bytes = new_bytes;
        let category_name = <String as FromSql<Text, Pg>>::from_sql(Some(elem_bytes))?;

        let _type = bytes.read_i32::<NetworkEndian>()?;
        let _size = bytes.read_i32::<NetworkEndian>()?;
        let hidden = <bool as FromSql<Bool, Pg>>::from_sql(Some(&[bytes.read_u8()?]))?;

        let _type = bytes.read_i32::<NetworkEndian>()?;
        let _size = bytes.read_i32::<NetworkEndian>()?;
        let protected = <bool as FromSql<Bool, Pg>>::from_sql(Some(&[bytes.read_u8()?]))?;

        Ok(NoteCategory {
            id: category_id,
            name: category_name,
            hidden: hidden,
            protected: protected,
        })
    }
}
