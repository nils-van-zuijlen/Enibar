#![allow(unused_imports)]

#[cfg(test)]
extern crate diesel;
#[cfg(test)]
extern crate gdk;
extern crate gtk;
extern crate rapi;
#[macro_use]
extern crate relm;
#[macro_use]
extern crate relm_derive;
#[macro_use]
extern crate relm_test;

mod widgets;
pub mod windows;
#[cfg(test)]
mod tests;
