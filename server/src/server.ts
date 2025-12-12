import { server } from './app';

const startServer = async () => {
  const port = 5050;

  server.listen(port, () => {
    console.log(`Listening on port: ${port}`);
  });
};


startServer();
