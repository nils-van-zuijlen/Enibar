use syn;
use quote::Tokens;

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
                        &self
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

            fn remove(self, conn: &::diesel::PgConnection) -> ::errors::Result<()> {
                ::diesel::ExecuteDsl::execute(
                    ::diesel::delete(&self),
                    conn
                )?;
                Ok(())
            }
        }
    )
}
