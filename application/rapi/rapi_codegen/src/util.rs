use syn::*;

pub fn list_value_of_attr_with_name<'a>(
    attrs: &'a [Attribute],
    name: &str,
) -> Option<Vec<&'a Ident>> {
    attr_with_name(attrs, name).map(|attr| list_value_of_attr(attr, name))
}

pub fn attr_with_name<'a>(attrs: &'a [Attribute], name: &str) -> Option<&'a Attribute> {
    attrs.into_iter().find(|attr| attr.name() == name)
}

fn list_value_of_attr<'a>(attr: &'a Attribute, name: &str) -> Vec<&'a Ident> {
    match attr.value {
        MetaItem::List(_, ref items) => items
            .iter()
            .map(|item| match *item {
                NestedMetaItem::MetaItem(MetaItem::Word(ref name)) => name,
                _ => panic!(r#"`{}` must be in the form `#[{}(something)]`"#, name, name),
            })
            .collect(),
        _ => panic!(r#"`{}` must be in the form `#[{}(something)]`"#, name, name),
    }
}

