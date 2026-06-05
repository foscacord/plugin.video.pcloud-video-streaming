# pCloud Video Streaming for Kodi

Kodi video plugin for streaming from [pCloud](https://www.pcloud.com).

## v1.5.2 — Login fix for Kodi 21 Omega

Login was broken on Kodi 21 Omega. pCloud deprecated the `userinfo` digest-auth endpoint — it no longer returns an `auth` token.

### Changes in `resources/lib/pcloudapi.py`

| Change | Detail |
|--------|--------|
| Auth endpoint | `userinfo` → `login` |
| Login params | Removed `logout=1` (invalidated sessions) |
| HTTP library | `urllib` / `build_opener` → `requests.Session()` |
| `ExecuteRequest` | Added `try/except` with `xbmc.log` on failure + HTTP status checks |
| Token expiry | 100 days → 1200 seconds (20 min, re-auths automatically) |
| `CheckIfAuthPresent` | Now auto-authenticates instead of raising exception |
| `PerformLogon` → `Logon` | Reads credentials from Kodi addon settings, handles encrypted password |
| `ListFolderContents` | Uses `listshares` for shared folders |
| `GetFileLink` | Retry logic + `skipfilename` param |
| `GetThumbnailLinks` | Returns list of URLs |
| `EncryptionDecryption` | New method for password handling |
| Removed | `DeleteFile`, `DeleteFolder`, `translateDate`, `errorCodeMapping` |

### Changes in `addon.xml`

| Change | Detail |
|--------|--------|
| Version | `1.5.1` → `1.5.2` |
| Description | Added "v1.5.2 fixes login on Kodi 21 Omega" |
| URL/source | Point to this fork |
| Removed | `email` field |

## Install

[Download ZIP](https://github.com/foscacord/plugin.video.pcloud-video-streaming/releases/latest) → Kodi → Add-ons → Install from zip file

## Credits

Original plugin by [Guido Domenici](https://github.com/gdomenici) · Matrix update by Carneal · Omega fix by [foscacord](https://github.com/foscacord)
