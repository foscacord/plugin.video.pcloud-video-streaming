# pCloud Video Streaming for Kodi

Stream videos from your [pCloud](https://www.pcloud.com) account directly in Kodi.

Works with free and paid pCloud accounts. Kodi 19 Matrix and later (including 21 Omega).

## Install

1. Download the ZIP from [Releases](https://github.com/foscacord/plugin.video.pcloud-video-streaming/releases/latest)
2. In Kodi: **Settings → System → Add-ons → Unknown sources → ON**
3. Home screen → **Add-ons** → package icon (top-left) → **Install from zip file**
4. Select the downloaded ZIP

## Login

On first launch, Kodi asks for your pCloud email and password.

> If pCloud blocks the login with "password incorrect" after a recent pCloud update, this is a known issue caused by pCloud changing their auth endpoint. v1.5.2 fixes this by switching to the correct `login` endpoint.

## What's new in v1.5.2

- Fixed login broken on Kodi 21 Omega (pCloud changed auth endpoint from `userinfo` to `login`)
- Removed `logout=1` param that was invalidating sessions prematurely

## Credits

Original plugin: [Guido Domenici](https://github.com/gdomenici) · Kodi Matrix update: Carneal · Kodi Omega fix: [foscacord](https://github.com/foscacord)
