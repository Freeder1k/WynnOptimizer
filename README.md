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

If you feel like it you can check out the optimizer code and adjust some parameters, but in my testing they don't have a big impact on performance. They are currently set to what works best for me (NVIDIA GTX 1080 GPU).
The wynnbuilder links that get output are all the same item type but you can just change that in wynnbuilder.
