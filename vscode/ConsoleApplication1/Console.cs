using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;


namespace ConsoleApplication1
{
    public class Console
    {
        public static void Main(string[] args)
        {
            int runtime = 180 * 5;
            //Initialize all the instances
            ShAgent agent = new ShAgent();
            VissimTools.InitVissimTools();

            int count = 0;

            while (true)
            {
                count++;

                //get initial state from vissim to agent
                double raw_state = VissimTools.vissimState(runtime); // TBD:

                // map to discrete  
                int state = (int)((raw_state - agent.get_min_state()) / agent.state_interval);

                // temp store of current q table for convergence check
                double[,] current_q_table = agent.q_table.Clone() as double[,];

                // get action
                int action = agent.get_action(state);

                // get reward

                int limSpd = (int)(agent.get_min_action() + action * agent.action_interval);
                double reward = VissimTools.vissimReward(runtime, limSpd);

                // update q table
                agent.update_q_table(state, action, reward);


                double diff = 0;

                for (int m = 0; m < agent.get_state_size(); m++)
                {
                    for (int n = 0; n < agent.get_action_size(); n++)
                    {
                        diff += Math.Abs(agent.q_table[m, n] - current_q_table[m, n]);
                    }  
                }

                System.Console.WriteLine("Run #:" + count + " ----------- " + diff + " (" + state + " : " + action + ")");

                // TBD: check if this is a good check
                if (diff < agent.convergence)
                {
                    break;
                }

                // System.Console.WriteLine(agent.q_table);

            }
            //get action 

            //get reward

            //update Q-table

            //next loop


            // VissimTools.InitVissimTools();
            // VissimTools.vissimStart()
        }
    }
}