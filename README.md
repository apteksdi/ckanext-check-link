[![Tests](https://github.com/DataShades/ckanext-check-link/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-check-link/actions)

# ckanext-check-link

Link checker for CKAN.

Provides API, CLI commands, and views for:

* checking availability of the file, refereed by resource
* checking availability of any arbitrary link.
* storing results of these checks
* visualizing stored results
* downloading a report based on the stored results

## Requirements

Compatibility with core CKAN versions:

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | yes         |
| 2.10         | yes         |

## Installation

1. Install `ckanext-check-link`
   ```
   pip install ckanext-check-link
   ```

1. Add `check_link` to the `ckan.plugins` setting in your CKAN config file.


## Config settings

```ini
# Allow any logged-in user to check links. This implies specific security issues,
# thus disabled by default.
# (optional, default: false).
ckanext.check_link.user_can_check_url = yes
```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
