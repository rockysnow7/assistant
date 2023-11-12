from agent.email_manager import EmailManager
from agent.openai_client import openai_client
from dotenv import load_dotenv
from openai.types.beta.threads.run import Run
from tenacity import retry, wait_fixed
from typing import Any

import json
import os
import pathlib


load_dotenv()


DEFAULT_CONFIG = {
    "email_address": "feyles@icloud.com",
    "thread_id": "", # openai thread id
    "voice": "nova",
}


class Agent:
    def __init__(self) -> None:
        # set up thread id and save it in `config.json`
        if "config.json" not in os.listdir():
            with open("config.json", "w+") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)

        try:
            with open("config.json", "r") as f:
                config = json.load(f)
            self.__thread = openai_client.beta.threads.retrieve(config["thread_id"])

        except:
            self.__thread = openai_client.beta.threads.create()

            with open("config.json", "r") as f:
                config = json.load(f)

            config["thread_id"] = self.__thread.id
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)

        with open("config.json", "r") as f:
            config = json.load(f)

        self.__assistant = openai_client.beta.assistants.retrieve(os.getenv("ASSISTANT_ID"))
        self.__email_manager = EmailManager()

    def __generate_image(
        self,
        prompt: str,
        style: str,
    ) -> str: # returns the url of the image
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="hd",
            style=style,
        )

        return response.data[0].url

    def __read_text(self, text: str, output_path: str) -> str:
        if os.path.exists(output_path):
            return "That path already exists, please choose a different path."

        with open("config.json", "r") as f:
            config = json.load(f)

        response = openai_client.audio.speech.create(
            model="tts-1-hd",
            voice=config["voice"],
            input=text,
        )
        pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        open(output_path, "w+").close()
        response.stream_to_file(output_path)

        return "Audio saved successfully."

    def __save_file(self, content: str, output_path: str) -> str:
        if os.path.exists(output_path):
            return "That path already exists, please choose a different path."

        pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w+") as f:
            f.write(content)
        return "File saved successfully."

    def __process_function_call(self, name: str, args: dict[str, Any]) -> str:
        if name == "send_email":
            return self.__email_manager.send_email(**args)
        if name == "generate_image":
            return self.__generate_image(**args)
        if name == "read_text":
            return self.__read_text(**args)
        if name == "save_file":
            return self.__save_file(**args)

    @retry(wait=wait_fixed(1))
    def __retrieve_run(self, run_id: str) -> Run | None:
        run = openai_client.beta.threads.runs.retrieve(
            run_id=run_id,
            thread_id=self.__thread.id,
        )
        if run.status in {"queued", "in_progress"}:
            raise Exception
        return run

    def __process_run(self, run: Run) -> str:
        if run.status == "completed":
            return run
        
        if run.status == "requires_action":
            calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            for call in calls:
                name = call.function.name
                print(f"{call.function.name=}, {call.function.arguments=}")
                args = call.function.arguments
                if args[-2:] == "}}": # sometimes openai returns json with an extra }, idk why but i wish they'd stop x
                    args = args[:-1]

                args = json.loads(args)
                output = self.__process_function_call(name, args)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output,
                })

            run = openai_client.beta.threads.runs.submit_tool_outputs(
                thread_id=self.__thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs,
            )
            return self.__process_run(run)

        run = self.__retrieve_run(run.id)
        return self.__process_run(run)

    def get_response(self, user_input: str) -> str:
        openai_client.beta.threads.messages.create(
            self.__thread.id,
            role="user",
            content=user_input,
        )
        run = openai_client.beta.threads.runs.create(
            thread_id=self.__thread.id,
            assistant_id=self.__assistant.id,
        )
        run = self.__process_run(run)

        messages = openai_client.beta.threads.messages.list(
            thread_id=self.__thread.id,
        )
        last_message = messages.data[0].content[0].text.value

        return last_message