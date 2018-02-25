use schema::panels;
use validator::Validate;
use products::models::Product;
use categories::models::Category;

#[derive(Debug, Queryable, AsChangeset, Identifiable, Model, Validate)]
#[table_name = "panels"]
pub struct Panel {
    pub id: i32,
    #[validate(custom = "::validators::not_empty")]
    pub name: String,
    pub hidden: bool,
}

#[derive(Insertable, Validate)]
#[table_name = "panels"]
pub struct NewPanel<'a> {
    #[validate(custom = "::validators::not_empty")]
    pub name: &'a str,
}

#[derive(Queryable, Debug)]
pub struct PanelItem {
    pub product: Product,
    pub category: Category,
}

#[derive(Debug, Clone)]
#[derive(SqlType)]
pub struct PanelProductsSql;

#[derive(Debug)]
pub struct PanelProduct {
    pub product_id: i32,
    pub product_name: String,
    pub price_label: String,
    pub price: ::BigDecimal,
}

#[derive(Queryable, Debug)]
pub struct PanelContent {
    pub panel_name: String,
    pub products: Vec<PanelProduct>,
    pub category_id: i32,
    pub category_name: String,
    pub category_alcoholic: bool,
    pub category_color: String,
}
