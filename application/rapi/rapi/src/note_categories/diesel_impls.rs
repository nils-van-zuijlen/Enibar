use byteorder::{NetworkEndian, ReadBytesExt};
use diesel::pg::Pg;
use diesel::sql_types::*;
use diesel::deserialize::FromSql;
use std::error::Error;

use super::models::{NoteCategory, NoteCategorySql};

impl HasSqlType<NoteCategorySql> for Pg {
    fn metadata(_lookup: &Self::MetadataLookup) -> Self::TypeMetadata {
        unreachable!()
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
