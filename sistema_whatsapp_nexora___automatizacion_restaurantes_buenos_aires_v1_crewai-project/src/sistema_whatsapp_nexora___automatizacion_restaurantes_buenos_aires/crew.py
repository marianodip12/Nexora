import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	ScrapeWebsiteTool
)
from sistema_whatsapp_nexora___automatizacion_restaurantes_buenos_aires.tools.whatsapp_messenger import WhatsAppMessengerTool
from sistema_whatsapp_nexora___automatizacion_restaurantes_buenos_aires.tools.restaurant_conversation_handler import RestaurantConversationHandlerTool
from sistema_whatsapp_nexora___automatizacion_restaurantes_buenos_aires.tools.deployment_files_generator import DeploymentFilesGeneratorTool




@CrewBase
class SistemaWhatsappNexoraAutomatizacionRestaurantesBuenosAiresCrew:
    """SistemaWhatsappNexoraAutomatizacionRestaurantesBuenosAires crew"""

    
    @agent
    def senior_python_developer___whatsapp_bot_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["senior_python_developer___whatsapp_bot_specialist"],
            
            
            tools=[				WhatsAppMessengerTool(),
				RestaurantConversationHandlerTool(),
				DeploymentFilesGeneratorTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
                
            ),
            
        )
    
    @agent
    def qa_engineer___chatbot_testing_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["qa_engineer___chatbot_testing_specialist"],
            
            
            tools=[				RestaurantConversationHandlerTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
                
            ),
            
        )
    
    @agent
    def devops_engineer___deployment_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["devops_engineer___deployment_specialist"],
            
            
            tools=[				DeploymentFilesGeneratorTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
                
            ),
            
        )
    
    @agent
    def ceo_agent___director_estrategico(self) -> Agent:
        
        return Agent(
            config=self.agents_config["ceo_agent___director_estrategico"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
                
            ),
            
        )
    
    @agent
    def sales_agent___prospector_de_restaurantes(self) -> Agent:
        
        return Agent(
            config=self.agents_config["sales_agent___prospector_de_restaurantes"],
            
            
            tools=[				WhatsAppMessengerTool(),
				ScrapeWebsiteTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
                
            ),
            
        )
    

    
    @task
    def build_flask_whatsapp_webhook_server(self) -> Task:
        return Task(
            config=self.tasks_config["build_flask_whatsapp_webhook_server"],
            markdown=False,
            
            
        )
    
    @task
    def prospecting_de_restaurantes_buenos_aires(self) -> Task:
        return Task(
            config=self.tasks_config["prospecting_de_restaurantes_buenos_aires"],
            markdown=False,
            
            
        )
    
    @task
    def test_all_conversation_flows(self) -> Task:
        return Task(
            config=self.tasks_config["test_all_conversation_flows"],
            markdown=False,
            
            
        )
    
    @task
    def generate_deployment_configuration(self) -> Task:
        return Task(
            config=self.tasks_config["generate_deployment_configuration"],
            markdown=False,
            
            
        )
    
    @task
    def supervision_estrategica_del_desarrollo(self) -> Task:
        return Task(
            config=self.tasks_config["supervision_estrategica_del_desarrollo"],
            markdown=False,
            
            
        )
    
    @task
    def actualizar_codigo_con_variables_reales(self) -> Task:
        return Task(
            config=self.tasks_config["actualizar_codigo_con_variables_reales"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the SistemaWhatsappNexoraAutomatizacionRestaurantesBuenosAires crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            chat_llm=LLM(model="openai/gpt-4o-mini"),
        )


