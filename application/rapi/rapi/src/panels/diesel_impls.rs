use byteorder::{NetworkEndian, ReadBytesExt};
use diesel::pg::Pg;
use diesel::sql_types::*;
use diesel::deserialize::FromSql;
use ::BigDecimal;
use std::error::Error;

use super::models::{PanelProduct, PanelProductsSql};

impl HasSqlType<PanelProductsSql> for Pg {
    fn metadata(_lookup: &Self::MetadataLookup) -> Self::TypeMetadata {
        unreachable!()
    }
}

impl FromSql<PanelProductsSql, Pg> for PanelProduct {
    fn from_sql(bytes: Option<&[u8]>) -> Result<Self, Box<Error + Send + Sync>> {
        let mut bytes = bytes.unwrap();
        let fields = bytes.read_i32::<NetworkEndian>()?;
        assert_eq!(fields, 5);

        let _type = bytes.read_i32::<NetworkEndian>()?;
        let size = bytes.read_i32::<NetworkEndian>()?;
        let (value, mut bytes) = bytes.split_at(size as usize);
        let product_id = <i32 as FromSql<Int4, Pg>>::from_sql(Some(value))?;

        let _type = bytes.read_i32::<NetworkEndian>()?;
        let size = bytes.read_i32::<NetworkEndian>()?;
        let (value, mut bytes) = bytes.split_at(size as usize);
        let product_name = <String as FromSql<Text, Pg>>::from_sql(Some(value))?;

        let _type = bytes.read_i32::<NetworkEndian>()?;
        let size = bytes.read_i32::<NetworkEndian>()?;
        let (value, mut bytes) = bytes.split_at(size as usize);
        let price_label = <String as FromSql<Text, Pg>>::from_sql(Some(value))?;

        let _type = bytes.read_i32::<NetworkEndian>()?;
        let size = bytes.read_i32::<NetworkEndian>()?;
        let (value, mut bytes) = bytes.split_at(size as usize);
        let price = <BigDecimal as FromSql<Numeric, Pg>>::from_sql(Some(value))?;

        let _type = bytes.read_i32::<NetworkEndian>()?;
        let _size = bytes.read_i32::<NetworkEndian>()?;
        let percentage = <BigDecimal as FromSql<Numeric, Pg>>::from_sql(Some(bytes))?;

        Ok(PanelProduct {
            product_id,
            product_name,
            price_label,
            price,
            percentage
        })
    }
}

