# pCloud Video Streaming for Kodi

Kodi video plugin that streams video from your [pCloud](https://www.pcloud.com) account.

## v1.5.2 — Login fix for Kodi 21 Omega

Login was broken on Kodi 21 Omega due to pCloud deprecating the `userinfo` auth endpoint.

**Fix:** `pcloudapi.py` now uses the `login` endpoint instead of `userinfo`.

### Install

[Download ZIP](https://github.com/foscacord/plugin.video.pcloud-video-streaming/releases/latest) → Kodi → Add-ons → Install from zip file

## Credits

Original plugin by [Guido Domenici](https://github.com/gdomenici) · Kodi Matrix update by Carneal · Omega fix by [foscacord](https://github.com/foscacord)
