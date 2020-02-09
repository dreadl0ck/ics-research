import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Data for plotting
t = [1,2,3,4,5,6,7,8,9,10]
s = [ 
    0.5293578505516052,
    0.4077320396900177,
    0.3176637887954712,
    0.25053125619888306,
    0.19991521537303925,
    0.16122758388519287,
    0.13124048709869385,
    0.10768652707338333,
    0.08896003663539886,
    0.07391022890806198
]

fig, ax = plt.subplots()
ax.plot(t, s)

ax.set(xlabel='epoch (#)', ylabel='loss',
       title='Loss over time, LSTM v10')
ax.grid()

fig.savefig("test.png")
plt.show()