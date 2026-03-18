A few core reasons:

**Training data cutoff**
Models are trained on data up to a certain date. APIs and libraries that were current during that period are well-represented in training data, so the model "knows" them better than newer alternatives.

**Representation bias in training data**
Older APIs have more examples on the internet — Stack Overflow answers, tutorials, blog posts, GitHub repos — accumulated over years. A deprecated API from 2018 might have 10x more code examples than its 2023 replacement, making the model more confident using it.

**Deprecation lag**
Even after an API is deprecated, code using it continues to exist online and gets forked, copied, and referenced. The model sees the old pattern reinforced long after it should have been replaced.

**No runtime feedback**
Models don't execute code during training or inference (generally), so they never learn "this broke" vs "this worked." A deprecated call that still technically functions looks identical to a current one in text.

**Documentation asymmetry**
Migration guides and deprecation notices are less common than original API documentation, so the "don't use this anymore" signal is weaker than the "here's how to use this" signal.

**Practical consequence**
This is why you should always:
- Specify the library version you're targeting
- Paste in relevant current docs or changelogs for fast-moving libraries
- Treat generated code involving external APIs as a starting point, not a final answer

My own knowledge cuts off in August 2025, so anything released or changed after that — I may get wrong too.