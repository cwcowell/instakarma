Instakarma is a tool for thanking or acknowledging other Instabasers by giving them karma.

Let's see how it works.

We're in a new Slack channel. Before using instakarma, you have to invite it to whatever channel or group direct message you're in. For privacy reasons, instakarma does _not_ work with 1-to-1 direct messages.

    @instakarma get in here

Now let's say my boss Jean Bond approved my last-minute PTO request, and I want to thank her.

    @jean ++

Now let's say Jean denied my attempt to expense a Ferrari. She's such a stickler for rules. I might try to take karma away from her...

    @jean --

But instakarma won't let you take karma away from your coworkers.

You can also give karma to people who aren't Instabase employees, or things that aren't people, like a place, a product, or a technology, or anything, really.

    pie++

If the thing you're giving karma to contains a space, use a hyphen instead.

    brighton-and-hove-albion-football-club++

We saw that you can't take karma away from Instabasers, but you can take it away from things...

    cilantro--
    the-entire-ruby-ecosystem--

So now you've seen the main operations.

Instakarma also has slash commands, similar to what you've probably used with other Slack apps.

Here's one...

    /instakarma my-stats

This command shows how much karma you have, the five people or things you've given the most karma to, and the five things you've taken away the most karma from.

In this case only 3 people have given me karma, which is kind of depressing.

Here's another command...

    /instakarma leaderboard

It lists anything that isn't a registered Slack user, along with how much karma they have. This lets you know what your coworkers are happy or upset about.

If you don't like the whole idea of granting or receiving karma, you can opt out of the system entirely...

    /instakarma opt-out

When you're opted out, you can't grant or receive karma.

    @melissa++

But you can change your mind and opt back in...

    /instakarma opt-in

And then everything goes back to normal...

    @melissa++

If you forget how to use instakarma, it's easy to get help.

    /instakarma help

There are also some administration tools for doing things like backing up the instakarma database, but those are only interesting to IT folks, so I won't bother showing them here.

    short-demos++

---

TODO:

* Populate DB for `/instakarma my-stats`

Jean gives me 5
Rosie gives me 4
Melissa gives me 4
Anshu gives me 1

I give karma to:

@jean ++ 23
tofu-and-marmite-omelettes++ 6
@anshu ++ 5
brighton-and-hove-albion-football-club++ 4
dolly-parton++ 3

cybertrucks-- 329
bridgerton-- 12
papercuts-- 7
the-entire-ruby-ecosystem-- 6
pumpkin-spice-dental-floss-- 3
