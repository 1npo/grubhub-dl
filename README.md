# grubhub-email-dl
A CLI tool that extracts data from your emails about your Grubhub orders, and exports it in various formats.

Only Gmail is supported. Support for Outlook (via the Graph API) is planned.

> [!IMPORTANT]
> This module can only process Grubhub emails that have the following subject lines, and are formatted the way Grubhub formats them as of ``2025-3-8``.
>   - Thanks for your <Restaurant> order ...
>   - Your order from <Restaurant> has been confirmed
>   - Your order was canceled
>   - Your order was updated
>   - You can now enjoy a discounted meal from Grubhub!
>   - You're approved for a Grubhub Guarantee Perk
>   - Enjoy $<N>.00 off your next Grubhub order

## Usage
Provide the path to the JSON file containing your Gmail/Outlook API credentials with the `--credentials-file` flag. Or you can set the path in the `GRUBHUB_EMAIL_DL_CREDENTIALS_FILE` environment variable before running `grubhub-email-dl`.

Example 1:
```console
grubhub-email-dl --email 'your.email@gmail.com' --credentials-file 'path_to_your_credentials_file.json'
```
```console
export GRUBHUB_EMAIL_DL_CREDENTIALS_FILE='path_to_your_credentials_file.json' grubhub-email-dl --email 'your.email@gmail.com'
```

## Parameters
...

## Dependencies
```console
pip install --upgrade keyring beautifulsoup4 google-api-python-client
    google-auth-oauthlib google-auth openpyxl pandas numpy
```
```
pip install --upgrade grubhub-email-dl
```
