# WynnOptimizer
---
Fast and customizeable programm to optimize wynncraft crafts.

## How to use:
---
**You need a CUDA-capable GPU to run this code!**
Installation info for the requirements can be found here (use pip or your preferred package manager to install the rest):
- [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
- [Numba](https://numba.readthedocs.io/en/stable/user/5minguide.html)
- [Cupy](https://docs.cupy.dev/en/stable/install.html)


### Optimizing a craft
1) Create a Config object that implements crafting.config.base.OptimalCrafterConfigBase (see crafting.config.example.spell_ring for an example)
2) Call crafting.optimizer.get_best_recipes_gpu(configObject)
3) Wait a bit depending on your gpu and how many Ingredients you include in your search.
4) Enjoy your results!

If you feel like it you can check out the optimizer code and adjust some parameters, but in my testing they don't have a big impact on performance. They are currently set to what works best for me.
The wynnbuilder links that get output are all the same item type but you can just change that in wynnbuilder.

### What to do if the crafter is too slow?
For me, the example (1.5 billion combinations) takes about 17s to execute on my laptop with a NVIDIA GeForce GTX 1050 GPU. You can use that as a benchmark to see how your pc compares to mine.

Since for each combination the score and the constraint function get evaluated, processing speed can be heavily impacted by these. Try to keep them as simple as possible. Check out the [CUDA fastmath capability in Numba](https://numba.readthedocs.io/en/stable/cuda/fastmath.html) if you want to use more complicated expressions.

Additionally, you can hand-pick ingredients to reduce the amount of combinations. The programm runs in O(n^6) time, where n is the number of ingredients.
