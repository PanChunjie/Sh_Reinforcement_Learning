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
            train(100);
        }


        public static void train(int epoch){
            int count = 0;            
            int runtime = 180 * 5;
            List<string> records = new List<string>();

            //Initialize all the instances
            ShAgent agent = new ShAgent();
            VissimTools.InitVissimTools();

            for (int e = 0; e < epoch; e++){

                count++;

                //get initial state from vissim to agent
                double raw_state = VissimTools.vissimState(runtime); // TBD:

                // map to discrete  
                int state = (int)((raw_state - agent.get_min_state()) / agent.state_interval);

                // temp store of current q table for convergence check
                double[,] current_q_table = agent.q_table.Clone() as double[,];

                // get action
                List<int> action = agent.get_action(state);

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

                records.Add(count + "," + diff + "," + state + "," + action[0] + "," + action[1]+ "," + reward)

                // ---------------------------

                // Set a variable to the Documents path.
                string outPutPath = "./"

                // Write the string array to a new file named "WriteLines.txt".
                using (StreamWriter outputFile = new StreamWriter(Path.Combine(docPath, "outputs.csv")))
                {
                    foreach (string line in records)
                        outputFile.WriteLine(line);
                }

                // ---------------------------

                // TBD: check if this is a good check
                if (diff < agent.convergence)
                {
                    break;
                }

            }
        }
    }
}