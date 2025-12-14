<div class="large-space-div" align="center">
  <img src="https://github.com/Bean-Pringles/CPlus/blob/main/Logo/cplus.png" alt="C+ Logo">
  <h3>Readable C</h3>
  <!-- The functional badge code -->
  <img alt="Static Badge" src="https://img.shields.io/github/stars/Bean-Pringles/Cplus"> <img alt="Static Badge" src="https://img.shields.io/badge/Language-Python-orange"> <img alt="Static Badge" src="https://img.shields.io/badge/OS-Windows, Linux, MacOS-green"> <img alt="Static Badge" src="https://img.shields.io/badge/Version-v0.2.3-purple"> <img alt="Static Badge" src="https://img.shields.io/badge/CPU-x86-yellow"> <img alt="Static Badge" src=https://img.shields.io/github/downloads/Bean-Pringles/Cplus/total.svg"> <img alt="Static Badge" src="https://img.shields.io/github/repo-size/Bean-Pringles/Cplus"> <img alt="Static Badge" src="https://img.shields.io/github/last-commit/Bean-Pringles/Cplus"> <img alt="Static Badge"src="https://img.shields.io/badge/404-Not%20Found-lightgrey">
  <h1> </h1>
</div>

<p>
C+ is a language that compiles directly to C. It maintains C's power while making it easier to understand and read. With one-to-one line translation, experienced C developers can translate their code into C+ with ease. The compiler, written in Python, has helpful and descriptive error messages to help the average developer. C+ is designed to get new people into C without the headaches, but with the power. Let's see what you can make!
</p>

<h1>Table Of Contents:</h1>
<ul>
  <li><a href="#example-syntax">Example Syntax</a></li>
  <li><a href="#features">Features</a></li>
  <li><a href="#setup">Setup</a></li>
  <li><a href="#license">License</a></li>
  <li><a href="#future-features">Future Features</a></li>
  <li><a href="#milestones">Milestones</a></li> <!-- This creates a list with each thing relating to a specific heading on it, so when you click the link, it scrolls down to that section. HTML is kinda easy, its just google searching what you need and formating it to you -->
</ul>


<h1 id="example-syntax">Example Syntax:</h1>
<h3>C+ Example of Hello World:</h3>

```C+
import stdio

fn main() {
    let hello: string = "Hello"
    let name: string = "Bob"

    print(hello + ", " + name + "!")
}
```
<h1> </h1>
<h3>C Example of Hello World:</h3>

```C
#include <stdio.h>

void main() {
    char hello[] = "Hello";
    char name[] = "Bob";

    printf("%s, %s!\n", hello, name);
}
```

<h1 id="features">Features:</h1>
<ul>
  <li>Compiled Directly to C</li>
  <li>Has one-to-one translation with C</li>
  <li>Does not require semicolons</li>
  <li>Pointers declared with "let*"</li>
  <li>Use "let [varname]: [var type]" instead of "int" or "char"</li>
  <li>Uses the GCC Compiler to compile the C</li>
  <li>If/Else statements do not require parentheses</li>
  <li>Void functions declared with "fn"</li>
  <li>Functions that return have a "-> [var type]" after the arguemnets</li>
  <li>Use "import [libray name]"</li>
  <li>Supports unsigned, long, short, or long long varibles with the following syntax "let x: int; [unsigned]; [long, short, long long]"</li>
  <li>Uses "print" instead of "printf"</li>
</ul>

<h1 id="setup">Setup:</h1>
<p>You can set up the compiler by navigating to setup.exe and running it. Make sure you run it as an admin. Then you can run the compiler by:</p>
<pre><code>cpx [filename].cpx [Flags: -r -d -c -v]</code></pre>

<h1 id="license">License:</h1>
<p>This project is licensed under the <a href="https://github.com/Bean-Pringles/CPlus/blob/main/LICENSE.md">Bean Pringles Compiler License (BPC License) v1.0</a></p>

<h1 id="future-features">Future Features:</h1>
<p>To check out future features, go to <a href="https://github.com/Bean-Pringles/CPlus/blob/main/TODO.txt">here</a>.</p>
<p>Things with a row of "-" underneath them are completed and added to the main repository</p>

<h1 id="milestones">Milestones:</h1>
<ui>
  <li>100 Commits!</li>
</ui>
