using Microsoft.Office.Interop.Excel;
using System;
using System.Collections.Generic;
using System.IO;
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

        public static void train(int epoch)
        {

            int count = 0;
            int action_runtime = 180 * 5;
            int state_runtime = 180 * 5;


            List<string> records = new List<string>();

            //Initialize all the instances
            ShAgent agent = new ShAgent();
            VissimTools.InitVissimTools();

            for (int e = 0; e < epoch; e++)
            {

                //get initial state from vissim to agent
                VissimTools.vissimRunFirstInterval();
                double raw_state = VissimTools.vissimState(count, state_runtime); // TBD:

                // map to discrete  
                if (raw_state < agent.get_min_state() || raw_state > agent.get_max_state())
                {
                    count++;
                    continue;
                }
                int state = (int)((raw_state - agent.get_min_state()) / agent.state_interval);

                // temp store of current q table for convergence check
                double[,] current_q_table = agent.q_table.Clone() as double[,];

                // get action
                List<int> action = agent.get_action(state);

                // get reward

                int limSpd = (int)(agent.get_min_action() + action[0] * agent.action_interval);
                double reward = VissimTools.vissimReward(action_runtime, limSpd);

                // update q table
                agent.update_q_table(state, action[0], reward);

                Application app = new Application { Visible = false };
                Workbook xBook = app.Workbooks._Open(@"D:\School11111111111111111111111111111\Coop2019\Summer\Capacity\Data\data.xlsx");
                Worksheet xSheet = (Worksheet)xBook.Sheets[1];
                Range c1 = (Range)app.Cells[count * 13 + 1, 1];
                Range c2 = (Range)app.Cells[count * 13 + 1 + 13 - 1, 10];
                Range range = app.get_Range(c1, c2);
                range.Value = agent.q_table;
                xBook.Save();
                xSheet = null;
                xBook.Close(0); //xlBook.Close(true); //Workbook.close(SaveChanges, filename, routeworkbook )
                app.Quit();


                double diff = 0;
                count++;

                for (int m = 0; m < agent.get_state_size(); m++)
                {
                    for (int n = 0; n < agent.get_action_size(); n++)
                    {
                        diff += Math.Abs(agent.q_table[m, n] - current_q_table[m, n]);
                    }
                }

                System.Console.WriteLine("Run #:" + count + " ----------- " + diff + " (" + state + " : " + action + ")");

                records.Add(count + "," + diff + "," + state + "," + action[0] + "," + action[1] + "," + reward);

                // ---------------------------

                // Set a variable to the Documents path.
                string outPutPath = "./";

                // Write the string array to a new file named "WriteLines.txt".
                using (StreamWriter outputFile = new StreamWriter(Path.Combine(outPutPath, "outputs.csv")))
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






