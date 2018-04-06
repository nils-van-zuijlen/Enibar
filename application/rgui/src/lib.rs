#![allow(unused_imports)]

extern crate gtk;
#[cfg(test)]
extern crate diesel;
#[cfg(test)]
extern crate gdk;
extern crate rapi;
#[macro_use] extern crate relm;
#[macro_use] extern crate relm_test;
#[macro_use] extern crate relm_derive;

mod widgets;
pub mod windows;
#[cfg(test)]
mod tests;
