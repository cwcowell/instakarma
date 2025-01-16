The easiest way to test these is to paste in the regex and this entire list into www.regex101.com

## Combinatorics:

* ++
* --
* ---

* no space between word and operator
* space between word and operator

* no word after
* word after without space between operator and word
* word after with space between operator and word

* no backticks
* immediate backticks
* distant backticks

* a's-b
* a\nb

## Valid users
<@([^\s`+-]+)>\s?(\+\+)(?![-+])


### Match

@Chris Cowell 2++
@Chris Cowell 2 ++
@Chris Cowell 2++ foo
@Chris Cowell 2 ++ foo

#### alternative for pasting into regex tester

<@a>++
<@a> ++
<@a>++ foo
<@a> ++ foo

### Don't match

@Chris Cowell 2--
@Chris Cowell 2---
@Chris Cowell 2 --
@Chris Cowell 2 ---
@Chris Cowell 2--foo
@Chris Cowell 2---foo
@Chris Cowell 2 --foo
@Chris Cowell 2 ---foo
@Chris Cowell 2-- foo
@Chris Cowell 2--- foo
@Chris Cowell 2 -- foo
@Chris Cowell 2 --- foo

`@Chris Cowell 2++`
`@Chris Cowell 2--`
`@Chris Cowell 2---`

`@Chris Cowell 2 ++`
`@Chris Cowell 2 --`
`@Chris Cowell 2 ---`

`@Chris Cowell 2++foo`
`@Chris Cowell 2--foo`
`@Chris Cowell 2---foo`

`@Chris Cowell 2 ++foo`
`@Chris Cowell 2 --foo`
`@Chris Cowell 2 ---foo`

`@Chris Cowell 2++ foo`
`@Chris Cowell 2-- foo`
`@Chris Cowell 2--- foo`

`@Chris Cowell 2 ++ foo`
`@Chris Cowell 2 -- foo`
`@Chris Cowell 2 --- foo`

`bar @Chris Cowell 2++`
`bar @Chris Cowell 2--`
`bar @Chris Cowell 2---`
  
`bar @Chris Cowell 2 ++`
`bar @Chris Cowell 2 --`
`bar @Chris Cowell 2 ---`
  
`bar @Chris Cowell 2++foo`
`bar @Chris Cowell 2--foo`
`bar @Chris Cowell 2---foo`
  
`bar @Chris Cowell 2 ++foo`
`bar @Chris Cowell 2 --foo`
`bar @Chris Cowell 2 ---foo`
  
`bar @Chris Cowell 2++ foo`
`bar @Chris Cowell 2-- foo`
`bar @Chris Cowell 2--- foo`
  
`bar @Chris Cowell 2 ++ foo`
`bar @Chris Cowell 2 -- foo`
`bar @Chris Cowell 2 --- foo`

#### alternative for pasting into regex tester

<@a>--
<@a>---
<@a> --
<@a> ---
<@a>--foo
<@a>---foo
<@a> --foo
<@a> ---foo
<@a>-- foo
<@a>--- foo
<@a> -- foo
<@a> --- foo

`<@a>++`
`<@a>--`
`<@a>---`

`<@a> ++`
`<@a> --`
`<@a> ---`

`<@a>++foo`
`<@a>--foo`
`<@a>---foo`

`<@a> ++foo`
`<@a> --foo`
`<@a> ---foo`

`<@a>++ foo`
`<@a>-- foo`
`<@a>--- foo`

`<@a> ++ foo`
`<@a> -- foo`
`<@a> --- foo`

`bar <@a>++`
`bar <@a>--`
`bar <@a>---`

`bar <@a> ++`
`bar <@a> --`
`bar <@a> ---`

`bar <@a>++foo`
`bar <@a>--foo`
`bar <@a>---foo`

`bar <@a> ++foo`
`bar <@a> --foo`
`bar <@a> ---foo`

`bar <@a>++ foo`
`bar <@a>-- foo`
`bar <@a>--- foo`

`bar <@a> ++ foo`
`bar <@a> -- foo`
`bar <@a> --- foo`

### Not sure/doesn't matter

@Chris Cowell 2++foo
@Chris Cowell 2 ++foo

#### alternative for pasting into regex tester

<@a>++foo
<@a> ++foo


## Invalid users

(?<!<)@([^\s`<>]+)(\+\+)(?![-+])

### Match

@a++
@a++ foo
@a-b++  [TODO: -b++ is recognized as an object]
@a-b++ foo  [TODO: -b++ is recognized as an object]
@a's-b++  [TODO: 's-b++ is recognized as an object]
@a's-b++ foo  [TODO: 's-b++ is recognized as an object]


### Don't match

@a ++
@a ++ foo
@a---
@a --
@a ---
@a--foo
@a---foo
@a --foo
@a ---foo
@a--- foo
@a -- foo
@a --- foo

@a-b ++
@a-b ++ foo
@a-b--
@a-b---
@a-b --
@a-b ---
@a-b--foo
@a-b---foo
@a-b --foo
@a-b ---foo
@a-b-- foo
@a-b--- foo
@a-b -- foo
@a-b --- foo

@a's-b ++
@a's-b ++ foo
@a's-b--
@a's-b---
@a's-b --
@a's-b ---
@a's-b--foo
@a's-b---foo
@a's-b --foo
@a's-b ---foo
@a's-b-- foo
@a's-b--- foo
@a's-b -- foo
@a's-b --- foo

`@a++`
`@a--`
`@a---`
`@a ++`
`@a --`
`@a ---`
`@a++foo`
`@a--foo`
`@a---foo`
`@a ++foo`
`@a --foo`
`@a ---foo`
`@a++ foo`
`@a-- foo`
`@a--- foo`
`@a ++ foo`
`@a -- foo`
`@a --- foo`
`bar @a++`
`bar @a--`
`bar @a---`
`bar @a ++`
`bar @a --`
`bar @a ---`
`bar @a++foo`
`bar @a--foo`
`bar @a---foo`
`bar @a ++foo`
`bar @a --foo`
`bar @a ---foo`
`bar @a++ foo`
`bar @a-- foo`
`bar @a--- foo`
`bar @a ++ foo`
`bar @a -- foo`
`bar @a --- foo`

### Not sure/doesn't matter
@a--
@a-- foo

---

## Objects
         
### Match
a++
a++ foo
a-b++
a--
a-- foo
a-b++ foo
a-b--
a-b-- foo
a's-b++
a's-b++ foo
a's-b--
a's-b-- foo

### Don't match
a ++
a ++ foo
a---
a --
a ---
a--foo
a---foo
a --foo
a ---foo
a--- foo
a -- foo
a --- foo
a-b ++
a-b ++ foo
a-b --
a-b ---
a-b--foo
a-b---foo
a-b --foo
a-b ---foo
a-b--- foo
a-b -- foo
a-b --- foo
a's-b ++
a's-b ++ foo
a's-b---
a's-b --
a's-b ---
a's-b--foo
a's-b---foo
a's-b --foo
a's-b ---foo
a's-b--- foo
a's-b -- foo
a's-b --- foo
`a++`
`a--`
`a---`
`a ++`
`a --`
`a ---`
`a++foo`
`a--foo`
`a---foo`
`a ++foo`
`a --foo`
`a ---foo`
`a++ foo`
`a-- foo`
`a--- foo`
`a ++ foo`
`a -- foo`
`a --- foo`
`bar a++`
`bar a--`
`bar a---`
`bar a ++`
`bar a --`
`bar a ---`
`bar a++foo`
`bar a--foo`
`bar a---foo`
`bar a ++foo`
`bar a --foo`
`bar a ---foo`
`bar a++ foo`
`bar a-- foo`
`bar a--- foo`
`bar a ++ foo`
`bar a -- foo`
`bar a --- foo`
`a's-b++`
`a's-b ++`
`a's-b++ foo`
`a's-b ++ foo`
`a's-b--`
`a's-b---`
`a's-b --`
`a's-b ---`
`a's-b--foo`
`a's-b---foo`
`a's-b --foo`
`a's-b ---foo`
`a's-b-- foo`
`a's-b--- foo`
`a's-b -- foo`
`a's-b --- foo`

### Not sure/don't care
a-b---
