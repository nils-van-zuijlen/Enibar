use syn;
use quote::Tokens;
use util::*;

pub fn derive_model(item: syn::DeriveInput) -> Tokens {
    let name = item.ident.clone();
    let fields: Vec<syn::Ident> = match item.body {
        syn::Body::Enum(..) => panic!("#[derive{Model})] cannot be used with enums"),
        syn::Body::Struct(ref body) => body.fields()
            .iter()
            .map(|f| f.ident.clone().unwrap())
            .collect(),
    };

    let fields2 = fields.clone(); // TODO: Find out if I can remove this and have fields twice in the expansion
    let primary_keys = list_value_of_attr_with_name(&item.attrs, "primary_key")
        .map(|v| v.into_iter().cloned().collect())
        .unwrap_or_else(|| vec![syn::Ident::new("id")]);

    let to_py = quote!(
        impl ::cpython::ToPyObject for #name {
            type ObjectType = ::cpython::PyDict;

            fn to_py_object(&self, py: ::cpython::Python) -> Self::ObjectType {
                let d = ::cpython::PyDict::new(py);
                #(d.set_item(py, stringify!(#fields), self.#fields2.clone()).unwrap();)*
                d
            }
        }
    );

    quote! (
        #to_py

        impl<'a> ::Model<'a> for #name
        {
            fn save(self, conn: &::diesel::PgConnection) -> ::errors::Result<Self> {
                if let Err(e) = self.validate() {
                    return Err(::errors::Error::from(::errors::ErrorKind::ValidationError(e)))
                }

                ::diesel::LoadDsl::get_result(
                    ::diesel::update(
                        ::diesel::FindDsl::find(
                            <Self as ::diesel::associations::HasTable>::table(),
                            (#(self.#primary_keys.clone()),*)
                        )
                    )
                    .set(&self),
                    conn
                )
                .map_err(|e| e.into())
            }

            fn all(conn: &::diesel::PgConnection) -> ::errors::Result<Vec<Self>> {
                ::diesel::LoadDsl::load(
                    <Self as ::diesel::associations::HasTable>::table(),
                    conn
                )
                .map_err(|e| e.into())
            }
        }
    )
}
