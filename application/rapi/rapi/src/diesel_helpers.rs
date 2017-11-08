use diesel::pg::Pg;
use diesel::types::*;
use diesel::Queryable;
use diesel::expression::AsExpression;
use diesel::expression::bound::Bound;
use diesel::row::Row;
use bigdecimal;
use std::ops::Deref;
use std::error::Error;
use std::io::Write;

#[derive(Debug, Clone)]
pub struct BigDecimal(pub bigdecimal::BigDecimal);

impl Deref for BigDecimal {
    type Target = bigdecimal::BigDecimal;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> AsExpression<Numeric> for &'a BigDecimal {
    type Expression = Bound<Numeric, &'a BigDecimal>;

    fn as_expression(self) -> Self::Expression {
        Bound::new(self)
    }
}

impl ToSql<Numeric, Pg> for BigDecimal {
    fn to_sql<W: Write>(
        &self,
        out: &mut ToSqlOutput<W, Pg>,
    ) -> Result<IsNull, Box<Error + Send + Sync>> {
        <bigdecimal::BigDecimal as ToSql<Numeric, Pg>>::to_sql(&self.0, out)
    }
}

impl FromSqlRow<Numeric, Pg> for BigDecimal {
    fn build_from_row<T: Row<Pg>>(row: &mut T) -> Result<Self, Box<Error + Send + Sync>> {
        Ok(BigDecimal(
            <bigdecimal::BigDecimal as FromSqlRow<Numeric, Pg>>::build_from_row(row)?,
        ))
    }
}

impl Queryable<Numeric, Pg> for BigDecimal {
    type Row = Self;
    fn build(row: Self) -> Self {
        row
    }
}
