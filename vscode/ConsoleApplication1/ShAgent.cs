using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using VISSIMLIB;
//using Microsoft.Office.Interop.Excel;
using System.Reflection;
using System.IO;


namespace ConsoleApplication1
{
    public class ShAgent
    {
        // hyperparameter
        public double learning_rate = 0.01;
        public double discount_factor = 0.9;
        public double epsilon = 0.3;
        public double convergence = 0.1;
        // action setup
        public static double min_action = 60; //TBD
        public static double max_action = 105; // TBD
        public static int action_size = 9; //TBD
        public double action_interval =
            (max_action - min_action) / action_size;
        // state setup
        public static double min_state = 3600; // TBD
        public static double max_state = 6000; // TBD
        public static int state_size = 13; // TBD
        public double state_interval =
            (max_state - min_state) / state_size;
        // q table
        public double[,] q_table = init_q_table(state_size, action_size);
       
        public ShAgent()
        {
        }

        public void MyMethod(int parameter1, string parameter2)
        {
            System.Console.WriteLine("First Parameter {0}, second parameter {1}",
                                                        parameter1, parameter2);
        }

        public static double[,] init_q_table(int state_size, int action_size)
        {
            // get the q-table initialized
            double[,] q_table = new double[13, 10]{
                {  4680,  3240,    3960,    2880 ,   2880  ,  3600  ,  3240   , 1800   , 4680   , 3600},
                {3960,   3240,    3600,    3240,    2160 ,   3960 ,   4680 ,   3960 ,   3600 ,   3600},
                { 3960,	3960,	5040	,3600,	2160,	4320,	3960,	3960,	3600,	4320},
                { 4320 , 4320 ,   4320   , 4320 ,   3600  ,  4320 ,   2520 ,   3600 ,   3960 ,   3240},
                {4320 ,  5040, 4320  ,  4680 ,   4320  ,  4680,    3240 ,   5040  ,  2880 ,   3600},
                { 4680 , 4680  ,  4680  ,  4320,   3960   , 1080   , 3960 ,   4680  ,  4320  ,  3960},
                {3960,   3960,    3960,    2880,    5040,    3600,    4680,    3600,    3240,    3960},
                { 4320,  3960,    3960 ,   5040,    3240,    5040,    3240,    3600,    3600,    3240},
                { 4320,  3600 ,   3600 ,   3960,    3600,    3960,    3600,    3240,    3960,    3960},
                { 3960,  3960,    4320 ,   3600,    4320,    2880,    1440,    3960,    3960,    4680},
                { 4320,  4680,    3960 ,   3600, 4680,    5040,    3240,    4680,    3960,    3240},
                { 3600,  3600,    4320,    5040,    3600,    4320,    4680,    3600,    4680,    5040},
                { 2160,  2160,   3600 ,  3960,    3600,    4680,    3600,    3600,    3960,    3960},
            };
      
            return q_table;
        }

        public void update_q_table(int state, int action, double reward)
        {
            // update Bellman equation
            double current_q = this.q_table[state, action];
            double new_q = reward; // add future step if we add furture actions
            this.q_table[state, action] = (1 - this.learning_rate) * current_q + this.learning_rate * new_q;
            //this.q_table[state, action] += this.learning_rate * (new_q - current_q);
        }

        public List<int> get_action(int state)
        {
            Random rand = new Random();
            List<int> action = new List<int>() { -1, -1 };

            // for-test: remove after
            double temp = rand.NextDouble();

            //if (rand.NextDouble() < this.epsilon)
            if (temp < this.epsilon)
            {
                // explore: select a random action base on eplison-greedy
                action[0] = rand.Next(action_size + 1);
                action[1] = 0;
            }
            else
            {
                // exploit: select the action with max value (future reward)
                double[] q_on_state = new double[action_size];

                for (int n = 0; n < action_size; n++)
                {

                    q_on_state[n] = q_table[state, n];
                }

                // TODO: consider to add randomness here
                action[0] = Array.IndexOf(q_on_state, q_on_state.Max());
                action[1] = 1;
            }
            return action;
        }
        /*
     public double[,] learn()
        {
            Env env = new Env();
            while (true)
            {
                double raw_state = env.get_state(); // TBD:

                // map to discrete  
                int state = (int)((raw_state - min_state) % this.state_interval);

                // temp store of current q table for convergence check
                double[,] current_q_table = q_table.Clone() as double[,];

                // get action
                int action = this.get_action(state);

                // get reward
                double reward = env.act(action);

                // update q table
                this.update_q_table(state, action, reward);


                double diff = 0;

                for (int m = 0; m < state_size; m++)
                {
                    for (int n = 0; n < action_size; n++)
                    {
                        diff += Math.Abs(this.q_table[m, n] - current_q_table[m, n]);
                    }

                    // TBD: check if this is a good check
                    if (diff < this.convergence)
                    {
                        return this.q_table;
                    }
                }
            }
        }
        */

        public double get_min_state()
        {
            return min_state;
        }
        public double get_max_state()
        {
            return max_state;
        }
        public double get_min_action()
        {
            return min_action;
        }

        public int get_state_size()
        {
            return state_size;
        }

        public int get_action_size()
        {
            return action_size;
        }
    }
}