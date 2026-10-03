---
title: Shortcodes
lead: Every shortcode the theme provides, in one place.
resources:
  - src: "photo-*.jpg"
    params:
      alt: Abstract green pattern
---
This page exists only in English, so the language switcher sends Swedish readers to the Swedish homepage.

## Button

{{< button url="/membership" >}}Become a member{{< /button >}}
{{< button url="/contact" style="secondary" >}}Contact us{{< /button >}}

## Consultation responses

Posts with `consultation` in their front matter, newest first:

{{< consultations >}}

## Notice

{{< notice >}}
The annual general meeting is on **25 March**.
{{< /notice >}}

{{< notice type="warning" >}}
Registration closes on Friday.
{{< /notice >}}

## Image and text

{{< image-text image="photo-1.jpg" alt="Abstract green pattern" side="right" >}}
Pair a picture with a short text. The image can sit on either side, at 50/50, 30/70 or 70/30.
{{< /image-text >}}

## Quote

{{< quote author="Internet Society" role="Mission statement" >}}
The Internet is for everyone.
{{< /quote >}}

## Stats

{{< stats >}}
{{< stat value="120+" label="Chapters worldwide" >}}
{{< stat value="1992" label="Year the Internet Society was founded" >}}
{{< stat value="100 000+" label="Members globally" >}}
{{< /stats >}}

## Columns

{{< columns >}}
{{< column >}}
### Open
The Internet should be available to everyone.
{{< /column >}}
{{< column >}}
### Secure
People should be able to trust the Internet.
{{< /column >}}
{{< /columns >}}

## Gallery

{{< gallery >}}

## Latest posts

{{< latest-posts count="4" >}}

## Upcoming events

{{< upcoming-events count="2" >}}

## Call to action

{{< cta title="Join the chapter" url="/membership" label="Become a member" >}}
Membership is free and open to everyone.
{{< /cta >}}
