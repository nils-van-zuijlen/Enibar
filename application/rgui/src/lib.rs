#![feature(proc_macro)]
#![allow(unused_imports)]

extern crate gtk;
#[cfg(test)]
extern crate gdk;
extern crate rapi;
#[macro_use] extern crate relm;
extern crate relm_attributes;
#[macro_use] extern crate relm_test;
#[macro_use] extern crate relm_derive;

mod widgets;
mod windows;
#[cfg(test)]
mod tests;
