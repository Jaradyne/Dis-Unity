# China government source-language handling — Scout notes

## What the official sites actually do

The State Council describes:
- `www.gov.cn` as the Chinese government website;
- `english.www.gov.cn` as its official English-language communication platform for the international community.

The English site is therefore not merely a browser-side script switch. It is a parallel official publication surface.

For the **State Council Gazette**, the English site explicitly says that when English and Chinese content differ, **the Chinese version prevails**.

## There is no verified universal public "language API"

Do not assume a documented government content API exists that accepts something like `?lang=en` / `?lang=zh`. The current Scout design should treat these as related publication surfaces, not one endpoint with a language parameter, unless an official API is later verified.

## Script and language

At the transport/text layer, Latin and Chinese characters can both be represented in Unicode; the important research distinction is not "different bytes mean different authority."

Record:
- `language`: `en`, `zh-Hans` where simplified Chinese is established;
- exact URL/host;
- publisher;
- publication/update time;
- whether the item is an official translation, separate official communication, Xinhua republication, or a machine translation made by Dis-Unity;
- relationship to a counterpart source when verified.

## Do not collapse translations into duplicates

Two pages about the same speech/event may:
- be published at different times;
- contain different editorial framing;
- omit detail;
- use terms with non-identical connotations;
- carry different formal authority.

Link them as counterparts rather than deleting one as a duplicate.

Suggested relation:

```json
{
  "source_id": "SRC-...",
  "language": "en",
  "counterpart_refs": ["SRC-..."],
  "translation_status": "official_english_surface | official_translation | separate_republication | machine_translation | unknown",
  "authority_note": "For State Council Gazette discrepancies, Chinese version prevails."
}
```

## Scout behavior

1. Prefer the source's original language when available.
2. Preserve official English separately for human readability and terminology comparison.
3. If Dis-Unity translates text itself, label the translation method/model.
4. Never attribute a machine translation to the Chinese government.
5. A difference between language versions is a possible interpretation/question lead, not automatically evidence of deception.
