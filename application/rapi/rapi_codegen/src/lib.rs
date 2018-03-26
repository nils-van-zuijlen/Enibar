#![recursion_limit = "256"]
extern crate proc_macro;
#[macro_use]
extern crate quote;
extern crate syn;

use proc_macro::TokenStream;
mod model;

#[proc_macro_derive(Model, attributes(primary_key))]
pub fn derive_insertable(input: TokenStream) -> TokenStream {
    expand_derive(input, model::derive_model)
}

fn expand_derive(input: TokenStream, f: fn(syn::DeriveInput) -> quote::Tokens) -> TokenStream {
    let item = syn::parse(input).unwrap();
    f(item).into()
}
