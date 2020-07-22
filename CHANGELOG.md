# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Enter here all the changes made to the development version

### Fixed

- Fixed so when payment link get's sent it contains the domain of the site

## [1.0.4] - 2020-05-27

- Admin: Fix payment link URL for notify event

## [1.0.3] - 2020-05-27

- Admin: Fix bug in email information

## [1.0.2] - 2020-05-27

- Admin: Add information about the email where payment link is sent to at
  order section.

## [1.0.1] - 2020-05-27

- Add option to send payment link from order admin. Sending payment link is
  triggered through notify event. Payment link is shown in special view with
  order details.
